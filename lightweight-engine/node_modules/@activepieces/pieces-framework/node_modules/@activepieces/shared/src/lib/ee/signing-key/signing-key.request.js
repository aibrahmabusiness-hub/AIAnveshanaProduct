"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AddSigningKeyRequestBody = void 0;
const zod_1 = require("zod");
exports.AddSigningKeyRequestBody = zod_1.z.object({
    displayName: zod_1.z.string(),
});
//# sourceMappingURL=signing-key.request.js.map