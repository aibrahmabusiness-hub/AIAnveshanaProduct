"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PropertySettings = exports.PropertyExecutionType = void 0;
const zod_1 = require("zod");
var PropertyExecutionType;
(function (PropertyExecutionType) {
    PropertyExecutionType["MANUAL"] = "MANUAL";
    PropertyExecutionType["DYNAMIC"] = "DYNAMIC";
})(PropertyExecutionType || (exports.PropertyExecutionType = PropertyExecutionType = {}));
exports.PropertySettings = zod_1.z.object({
    type: zod_1.z.nativeEnum(PropertyExecutionType),
    schema: zod_1.z.any().optional(),
});
//# sourceMappingURL=property.js.map