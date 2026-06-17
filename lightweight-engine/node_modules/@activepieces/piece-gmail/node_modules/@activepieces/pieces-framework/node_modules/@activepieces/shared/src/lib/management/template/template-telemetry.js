"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TemplateTelemetryEvent = exports.TemplateTelemetryEventType = void 0;
const zod_1 = require("zod");
var TemplateTelemetryEventType;
(function (TemplateTelemetryEventType) {
    TemplateTelemetryEventType["VIEW"] = "VIEW";
    TemplateTelemetryEventType["INSTALL"] = "INSTALL";
    TemplateTelemetryEventType["ACTIVATE"] = "ACTIVATE";
    TemplateTelemetryEventType["DEACTIVATE"] = "DEACTIVATE";
    TemplateTelemetryEventType["EXPLORE_VIEW"] = "EXPLORE_VIEW";
})(TemplateTelemetryEventType || (exports.TemplateTelemetryEventType = TemplateTelemetryEventType = {}));
const ViewEvent = zod_1.z.object({
    eventType: zod_1.z.literal(TemplateTelemetryEventType.VIEW),
    templateId: zod_1.z.string(),
});
const InstallEvent = zod_1.z.object({
    eventType: zod_1.z.literal(TemplateTelemetryEventType.INSTALL),
    templateId: zod_1.z.string(),
    userId: zod_1.z.string(),
});
const ActivateEvent = zod_1.z.object({
    eventType: zod_1.z.literal(TemplateTelemetryEventType.ACTIVATE),
    templateId: zod_1.z.string(),
    flowId: zod_1.z.string(),
});
const DeactivateEvent = zod_1.z.object({
    eventType: zod_1.z.literal(TemplateTelemetryEventType.DEACTIVATE),
    templateId: zod_1.z.string(),
    flowId: zod_1.z.string(),
});
const ExploreViewEvent = zod_1.z.object({
    eventType: zod_1.z.literal(TemplateTelemetryEventType.EXPLORE_VIEW),
    userId: zod_1.z.string().optional(),
});
exports.TemplateTelemetryEvent = zod_1.z.discriminatedUnion('eventType', [
    InstallEvent,
    ActivateEvent,
    DeactivateEvent,
    ViewEvent,
    ExploreViewEvent,
]);
//# sourceMappingURL=template-telemetry.js.map