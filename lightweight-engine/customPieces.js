const { createPiece, createAction, Property } = require("@activepieces/pieces-framework");

const jira = createPiece({
    displayName: 'Jira',
    name: '@activepieces/piece-jira',
    logoUrl: 'https://cdn.iconscout.com/icon/free/png-256/jira-3628778-3030225.png',
    authors: [],
    actions: [
        createAction({
            name: 'create_issue',
            displayName: 'Create Issue',
            description: 'Create a new issue in Jira',
            props: {
                projectKey: Property.ShortText({ displayName: 'Project Key', required: true }),
                summary: Property.ShortText({ displayName: 'Summary', required: true }),
                description: Property.LongText({ displayName: 'Description', required: false })
            },
            async run(context) {
                console.log(`[JIRA] Creating issue in ${context.propsValue.projectKey}: ${context.propsValue.summary}`);
                return { success: true, message: `Created issue in ${context.propsValue.projectKey}`, issueId: `PROJ-${Math.floor(Math.random() * 1000)}` };
            }
        })
    ],
    triggers: []
});

const servicenow = createPiece({
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
});

const coreLogic = createPiece({
    displayName: 'Core Logic',
    name: 'core',
    logoUrl: 'https://cdn-icons-png.flaticon.com/512/8202/8202354.png',
    authors: [],
    actions: [
        createAction({
            name: 'branch',
            displayName: 'Branch',
            description: 'Evaluate a condition',
            props: {
                condition: Property.ShortText({ displayName: 'Condition', description: 'Enter condition to evaluate (e.g. true, false, or variable output)', required: true })
            },
            async run(context) {
                const val = context.propsValue.condition;
                console.log(`[Core Logic] Evaluating branch condition: ${val}`);
                let conditionMet = false;
                if (val === 'true' || val === true) conditionMet = true;
                return { conditionMet, rawInput: val };
            }
        }),
        createAction({
            name: 'loop',
            displayName: 'Loop',
            description: 'Basic Loop configuration step',
            props: {
                items: Property.ShortText({ displayName: 'Items', description: 'Items to loop over', required: true })
            },
            async run(context) {
                console.log(`[Core Logic] Starting loop with items: ${context.propsValue.items}`);
                return { loopStarted: true, items: context.propsValue.items };
            }
        })
    ],
    triggers: []
});

module.exports = { jira, servicenow, salesforce, coreLogic };
