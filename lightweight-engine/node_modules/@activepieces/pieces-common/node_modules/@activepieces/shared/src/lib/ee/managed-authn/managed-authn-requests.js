"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ManagedAuthnRequestBody = void 0;
const zod_1 = require("zod");
exports.ManagedAuthnRequestBody = zod_1.z.object({
    //if you change this you need to update the embed-sdk I can't import it there because it can't have dependencies
    externalAccessToken: zod_1.z.string(),
});
//# sourceMappingURL=managed-authn-requests.js.map