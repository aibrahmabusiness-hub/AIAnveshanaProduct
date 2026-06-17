"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UpdateTemplatesCategoriesFlagRequestBody = void 0;
const zod_1 = require("zod");
exports.UpdateTemplatesCategoriesFlagRequestBody = zod_1.z.object({
    value: zod_1.z.array(zod_1.z.string()),
});
//# sourceMappingURL=flag.requests.js.map