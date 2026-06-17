"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GetVariableForWorkerRequestParams = exports.RevealVariableResponse = exports.ListVariablesRequestQuery = void 0;
const zod_1 = require("zod");
exports.ListVariablesRequestQuery = zod_1.z.object({
    projectId: zod_1.z.string(),
    cursor: zod_1.z.string().optional(),
    limit: zod_1.z.coerce.number().optional(),
    name: zod_1.z.string().optional(),
});
exports.RevealVariableResponse = zod_1.z.object({
    value: zod_1.z.string(),
});
exports.GetVariableForWorkerRequestParams = zod_1.z.object({
    name: zod_1.z.string(),
});
//# sourceMappingURL=read-variable-request.js.map