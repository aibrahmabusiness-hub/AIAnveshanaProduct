"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.McpTrigger = exports.McpProperty = exports.McpPropertyType = void 0;
const zod_1 = require("zod");
var McpPropertyType;
(function (McpPropertyType) {
    McpPropertyType["TEXT"] = "Text";
    McpPropertyType["BOOLEAN"] = "Boolean";
    McpPropertyType["DATE"] = "Date";
    McpPropertyType["NUMBER"] = "Number";
    McpPropertyType["ARRAY"] = "Array";
    McpPropertyType["OBJECT"] = "Object";
})(McpPropertyType || (exports.McpPropertyType = McpPropertyType = {}));
exports.McpProperty = zod_1.z.object({
    name: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    type: zod_1.z.string(),
    required: zod_1.z.boolean(),
});
exports.McpTrigger = zod_1.z.object({
    pieceName: zod_1.z.string(),
    triggerName: zod_1.z.string(),
    input: zod_1.z.object({
        toolName: zod_1.z.string(),
        toolDescription: zod_1.z.string(),
        inputSchema: zod_1.z.array(exports.McpProperty),
        returnsResponse: zod_1.z.boolean(),
    }),
});
//# sourceMappingURL=mcp-piece.js.map