import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\lightweight-engine\customPieces.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the dummy servicenow with the full definition
old_sn = """const servicenow = createPiece({
    displayName: 'ServiceNow',
    name: '@activepieces/piece-servicenow',
    logoUrl: 'https://cdn.iconscout.com/icon/free/png-256/servicenow-3629048-3030310.png',
    authors: [],
    actions: [
        createAction({
            name: 'create_incident',
            displayName: 'Create Incident',
            description: 'Creates a new incident record',
            props: {
                short_description: Property.ShortText({ displayName: 'Short Description', required: true }),
                caller_id: Property.ShortText({ displayName: 'Caller', required: false }),
                urgency: Property.ShortText({ displayName: 'Urgency', required: false })
            },
            async run(context) {
                console.log(`[ServiceNow] Creating incident: ${context.propsValue.short_description}`);
                return { success: true, incidentNumber: `INC${Math.floor(Math.random() * 1000000)}` };
            }
        })
    ],
    triggers: []
});"""

new_sn_and_sf = """const servicenow = createPiece({
    displayName: 'ServiceNow',
    name: '@activepieces/piece-servicenow',
    logoUrl: 'https://cdn.iconscout.com/icon/free/png-256/servicenow-3629048-3030310.png',
    authors: [],
    actions: [
        createAction({
            name: 'servicenow_incidents::create_incident',
            displayName: 'Create Incident',
            description: 'Creates a new incident record in ServiceNow',
            props: {
                short_description: Property.ShortText({ displayName: 'Short Description', required: true }),
                description: Property.ShortText({ displayName: 'Description', required: true }),
                urgency: Property.ShortText({ displayName: 'Urgency (1, 2, or 3)', required: false }),
                severity: Property.ShortText({ displayName: 'Severity (1, 2, or 3)', required: false })
            },
            async run(context) { return { success: true, message: "Handled by Python Unified Architecture" }; }
        }),
        createAction({
            name: 'servicenow_incidents::get_incidents',
            displayName: 'Get Recent Incidents',
            description: 'Retrieve latest incidents',
            props: {
                limit: Property.ShortText({ displayName: 'Limit', required: false }),
                state: Property.ShortText({ displayName: 'State Filter', required: false })
            },
            async run(context) { return { success: true, message: "Handled by Python Unified Architecture" }; }
        }),
        createAction({
            name: 'servicenow_incidents::update_incident',
            displayName: 'Update Incident',
            description: 'Update state or add comments to an incident',
            props: {
                sys_id: Property.ShortText({ displayName: 'System ID', required: true }),
                state: Property.ShortText({ displayName: 'New State', required: true }),
                comments: Property.ShortText({ displayName: 'Comments', required: false })
            },
            async run(context) { return { success: true, message: "Handled by Python Unified Architecture" }; }
        }),
        createAction({
            name: 'servicenow_tables::query_table',
            displayName: 'Query Any Table',
            description: 'Query records from a ServiceNow table generically',
            props: {
                table_name: Property.ShortText({ displayName: 'Table Name', required: true }),
                query: Property.ShortText({ displayName: 'Query String', required: false }),
                limit: Property.ShortText({ displayName: 'Limit', required: false })
            },
            async run(context) { return { success: true, message: "Handled by Python Unified Architecture" }; }
        })
    ],
    triggers: []
});

const salesforce = createPiece({
    displayName: 'Salesforce',
    name: '@activepieces/piece-salesforce',
    logoUrl: 'https://cdn.iconscout.com/icon/free/png-256/salesforce-282298.png',
    authors: [],
    actions: [
        createAction({
            name: 'salesforce_query::query_salesforce',
            displayName: 'Query Records',
            description: 'Run a SOQL query against Salesforce CRM',
            props: {
                query: Property.ShortText({ displayName: 'SOQL Query', required: true })
            },
            async run(context) { return { success: true, message: "Handled by Python Unified Architecture" }; }
        }),
        createAction({
            name: 'salesforce_create::create_salesforce_record',
            displayName: 'Create Record',
            description: 'Create a new record in Salesforce CRM',
            props: {
                object_type: Property.ShortText({ displayName: 'Object Type', required: true }),
                data: Property.ShortText({ displayName: 'JSON Data', required: true })
            },
            async run(context) { return { success: true, message: "Handled by Python Unified Architecture" }; }
        })
    ],
    triggers: []
});"""

content = content.replace(old_sn, new_sn_and_sf)

# Make sure salesforce is exported
old_export = "module.exports = { jira, servicenow, coreLogic };"
new_export = "module.exports = { jira, servicenow, salesforce, coreLogic };"
content = content.replace(old_export, new_export)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched customPieces.js successfully.")
