"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TriggerEventWithPayload = exports.TriggerEvent = void 0;
const zod_1 = require("zod");
exports.TriggerEvent = zod_1.z.object({
    id: zod_1.z.string(),
    projectId: zod_1.z.string(),
    flowId: zod_1.z.string(),
    sourceName: zod_1.z.string(),
    fileId: zod_1.z.string(),
});
exports.TriggerEventWithPayload = exports.TriggerEvent.extend({
    payload: zod_1.z.unknown(),
});
//# sourceMappingURL=trigger-event.js.map