export declare const requestAction: (conversationId: string, context: any) => Promise<{
    action: any;
    payload: {
        type: string;
        user: {
            id: string | undefined;
            username: string;
            name: string;
            team_id: string | undefined;
        };
        container: {
            type: string;
            message_ts: string | undefined;
            channel_id: string | undefined;
            is_ephemeral: boolean;
        };
        trigger_id: string;
        team: {
            id: string | undefined;
            domain: string;
        };
        channel: {
            id: string | undefined;
            name: string;
        };
        message: import("@slack/web-api/dist/types/response/ChatPostMessageResponse").ChatPostMessageResponseMessage | undefined;
        state: {};
        actions: {
            action_id: string;
            block_id: string;
            value: string;
            style: string;
            type: string;
            action_ts: string;
        }[];
    };
} | {
    action: string;
    payload: any;
}>;
//# sourceMappingURL=request-action.d.ts.map