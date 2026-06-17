"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreateMCPServerFromStepParams = void 0;
const zod_1 = require("zod");
exports.CreateMCPServerFromStepParams = zod_1.z.object({
    flowId: zod_1.z.string(),
    flowVersionId: zod_1.z.string(),
    stepName: zod_1.z.string(),
});
//# sourceMappingURL=flow-mcp.requests.js.map