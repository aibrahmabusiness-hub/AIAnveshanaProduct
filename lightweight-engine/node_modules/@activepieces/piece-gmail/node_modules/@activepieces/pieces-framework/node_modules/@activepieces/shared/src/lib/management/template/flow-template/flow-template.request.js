"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GetFlowTemplateRequestQuery = void 0;
const zod_1 = require("zod");
exports.GetFlowTemplateRequestQuery = zod_1.z.object({
    versionId: zod_1.z.string().optional(),
});
//# sourceMappingURL=flow-template.request.js.map