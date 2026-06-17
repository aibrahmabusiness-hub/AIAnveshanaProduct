"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TriggerStatusReport = exports.TriggerRunStatus = void 0;
const zod_1 = require("zod");
var TriggerRunStatus;
(function (TriggerRunStatus) {
    TriggerRunStatus["COMPLETED"] = "COMPLETED";
    TriggerRunStatus["FAILED"] = "FAILED";
    TriggerRunStatus["INTERNAL_ERROR"] = "INTERNAL_ERROR";
    TriggerRunStatus["TIMED_OUT"] = "TIMED_OUT";
})(TriggerRunStatus || (exports.TriggerRunStatus = TriggerRunStatus = {}));
exports.TriggerStatusReport = zod_1.z.object({
    pieces: zod_1.z.record(zod_1.z.string(), zod_1.z.object({
        dailyStats: zod_1.z.record(zod_1.z.string(), zod_1.z.object({
            success: zod_1.z.number(),
            failure: zod_1.z.number(),
        })),
        totalRuns: zod_1.z.number(),
    })),
});
//# sourceMappingURL=trigger-run.js.map