param location string = resourceGroup().location
param vmName string = 'flaskvm'
param adminUsername string
@secure()
param adminPassword string

resource openai 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'my-openai-instance'
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    apiProperties: {
      // Add deployment config as needed
    }
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: 'flask-vnet'
  location: location
  properties: {
    addressSpace: { addressPrefixes: [ '10.0.0.0/16' ] }
    subnets: [
      { name: 'default'; properties: { addressPrefix: '10.0.0.0/24' } }
    ]
  }
}

resource publicIp 'Microsoft.Network/publicIPAddresses@2023-04-01' = {
  name: 'flask-public-ip'
  location: location
  properties: {
    publicIPAllocationMethod: 'Dynamic'
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2023-04-01' = {
  name: 'flask-nic'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: { id: vnet.properties.subnets[0].id }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: { id: publicIp.id }
        }
      }
    ]
  }
}

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-04-01' = {
  name: 'flask-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'Allow-Flask'
        properties: {
          priority: 1001
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '5000'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

resource nsgAssoc 'Microsoft.Network/networkInterfaces/networkSecurityGroup@2023-04-01' = {
  parent: nic
  properties: {
    id: nsg.id
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2023-07-01' = {
  name: vmName
  location: location
  properties: {
    hardwareProfile: { vmSize: 'Standard_B1s' }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      adminPassword: adminPassword
      linuxConfiguration: { disablePasswordAuthentication: false }
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: 'UbuntuServer'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
      }
    }
    networkProfile: {
      networkInterfaces: [
        { id: nic.id }
      ]
    }
    identity: {
        type: 'SystemAssigned'
    }
  }
}

resource openaiAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(vm.id, 'OpenAIUser')
  scope: openai
  properties: {
    principalId: vm.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'c12c1c16-33a1-487b-954d-41c89c60f349') // Cognitive Services User
    principalType: 'ServicePrincipal'
  }
}

resource customScript 'Microsoft.Compute/virtualMachines/extensions@2023-07-01' = {
  name: 'install-flask-app'
  parent: vm
  properties: {
    publisher: 'Microsoft.Azure.Extensions'
    type: 'CustomScript'
    typeHandlerVersion: '2.1'
    autoUpgradeMinorVersion: true
    settings: {
      fileUris: [
        // Add URLs to your .py files in a storage account or GitHub raw links
        'https://raw.githubusercontent.com/<your-repo>/<branch>/Service/docubuddy-api.py'
      ]
      commandToExecute: '''
        sudo apt-get update
        sudo apt-get install -y python3-pip
        pip3 install flask requests azure-identity azure-ai-openai python-dotenv
        nohup python3 docubuddy-api.py --host 0.0.0.0 --port 5000 &
      '''
    }
  }
}

output publicIpAddress string = publicIp.properties.ipAddress