targetScope = 'resourceGroup'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Name prefix for all resources (lowercase, alphanumeric). Used to construct globally-unique names where required.')
param namePrefix string = 'dsf'

@description('Container image for API (e.g., <acr>.azurecr.io/dsf-api:latest). Filled by azd during deploy.')
param apiImage string

@description('Container image for Worker (e.g., <acr>.azurecr.io/dsf-worker:latest). Filled by azd during deploy.')
param workerImage string

@description('Minimum replicas for API app')
param apiMinReplicas int = 1

@description('Maximum replicas for API app')
param apiMaxReplicas int = 3

@description('Minimum replicas for Worker app')
param workerMinReplicas int = 1

@description('Maximum replicas for Worker app')
param workerMaxReplicas int = 3

var rg = resourceGroup().name
var unique = uniqueString(subscription().id, rg, namePrefix)

// ---------- Log Analytics ----------
resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: toLower('${namePrefix}-law-${unique}')
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Workspace shared key for Container Apps env diagnostics
var lawKeys = listKeys(law.id, '2020-08-01')

// ---------- Application Insights (workspace-based) ----------
resource appi 'microsoft.insights/components@2020-02-02' = {
  name: toLower('${namePrefix}-appi-${unique}')
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Bluefield'
    WorkspaceResourceId: law.id
  }
}

// ---------- Container Registry ----------
resource acr 'Microsoft.ContainerRegistry/registries@2023-06-01-preview' = {
  name: toLower(replace('${namePrefix}${unique}acr', '-', ''))
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    dataEndpointEnabled: false
  }
}

// ---------- User Assigned Managed Identity ----------
resource uami 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: toLower('${namePrefix}-uami-${unique}')
  location: location
}

// ---------- Key Vault (RBAC-enabled) ----------
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: toLower('${namePrefix}-kv-${unique}')
  location: location
  properties: {
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enabledForTemplateDeployment: true
    publicNetworkAccess: 'Enabled'
  }
}

// ---------- Azure Cache for Redis (Basic for dev) ----------
resource redis 'Microsoft.Cache/Redis@2023-08-01' = {
  name: toLower('${namePrefix}-redis-${unique}')
  location: location
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}

var redisHost = '${redis.name}.redis.cache.windows.net'
var redisKeys = listKeys(redis.id, '2023-08-01')
var redisPrimaryKey = redisKeys.primaryKey
var redisConnectionString = 'rediss://:${redisPrimaryKey}@${redisHost}:6380/0'

// Store Redis connection string in Key Vault as a secret
resource kvSecretRedis 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'DSF-REDIS-URL'
  parent: kv
  properties: {
    value: redisConnectionString
    contentType: 'text/plain'
  }
}

// ---------- Role Assignments ----------
// UAMI -> AcrPull on ACR
resource acrPullRA 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, 'AcrPull', uami.id)
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: uami.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// UAMI -> Key Vault Secrets User on KV
resource kvSecretsUserRA 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(kv.id, 'KeyVaultSecretsUser', uami.id)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: uami.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// ---------- Container Apps Managed Environment ----------
resource cae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: toLower('${namePrefix}-cae-${unique}')
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: lawKeys.primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

// ---------- Container App: API ----------
resource ca_api 'Microsoft.App/containerApps@2024-03-01' = {
  name: toLower('${namePrefix}-api-${unique}')
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${uami.id}': {}
    }
  }
  properties: {
    environmentId: cae.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: [ '*' ]
        }
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: uami.id
        }
      ]
      secrets: [
        {
          name: 'dsf-redis-url'
          identity: uami.id
          keyVaultUrl: uri(kv.properties.vaultUri, 'secrets/DSF-REDIS-URL')
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          env: [
            {
              name: 'DSF_DB'
              value: 'sqlite'
            }
            {
              name: 'DSF_QUEUE'
              value: 'redis'
            }
            {
              name: 'DSF_KEYVAULT_ENABLED'
              value: 'true'
            }
            {
              name: 'DSF_KEYVAULT_URI'
              value: kv.properties.vaultUri
            }
            {
              name: 'DSF_REDIS_URL'
              secretRef: 'dsf-redis-url'
            }
          ]
          resources: {
            cpu: 1
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: apiMinReplicas
        maxReplicas: apiMaxReplicas
      }
    }
  }
  dependsOn: [ acrPullRA, kvSecretsUserRA, kvSecretRedis ]
}

// ---------- Container App: Worker ----------
resource ca_worker 'Microsoft.App/containerApps@2024-03-01' = {
  name: toLower('${namePrefix}-worker-${unique}')
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${uami.id}': {}
    }
  }
  properties: {
    environmentId: cae.id
    configuration: {
      registries: [
        {
          server: acr.properties.loginServer
          identity: uami.id
        }
      ]
      secrets: [
        {
          name: 'dsf-redis-url'
          identity: uami.id
          keyVaultUrl: uri(kv.properties.vaultUri, 'secrets/DSF-REDIS-URL')
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'worker'
          image: workerImage
          env: [
            {
              name: 'DSF_DB'
              value: 'sqlite'
            }
            {
              name: 'DSF_QUEUE'
              value: 'redis'
            }
            {
              name: 'DSF_KEYVAULT_ENABLED'
              value: 'true'
            }
            {
              name: 'DSF_KEYVAULT_URI'
              value: kv.properties.vaultUri
            }
            {
              name: 'DSF_REDIS_URL'
              secretRef: 'dsf-redis-url'
            }
          ]
          resources: {
            cpu: 1
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: workerMinReplicas
        maxReplicas: workerMaxReplicas
      }
    }
  }
  dependsOn: [ acrPullRA, kvSecretsUserRA, kvSecretRedis ]
}

output containerAppsEnvironmentName string = cae.name
output apiAppFqdn string = ca_api.properties.configuration.ingress.fqdn
output workerAppName string = ca_worker.name
output keyVaultName string = kv.name
output acrLoginServer string = acr.properties.loginServer
output appInsightsName string = appi.name
