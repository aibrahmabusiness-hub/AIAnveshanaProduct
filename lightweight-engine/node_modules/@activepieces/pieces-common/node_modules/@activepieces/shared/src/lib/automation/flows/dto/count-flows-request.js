"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CountFlowsRequest = void 0;
const zod_1 = require("zod");
exports.CountFlowsRequest = zod_1.z.object({
    projectId: zod_1.z.string(),
    folderId: zod_1.z.string().optional(),
});
//# sourceMappingURL=count-flows-request.js.map