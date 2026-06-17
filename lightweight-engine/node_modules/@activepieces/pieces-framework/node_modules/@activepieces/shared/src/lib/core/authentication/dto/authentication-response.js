"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthenticationResponse = exports.UserWithoutPassword = void 0;
const zod_1 = require("zod");
const user_1 = require("../../user/user");
const user_identity_1 = require("../user-identity");
exports.UserWithoutPassword = user_1.User.pick({ id: true, platformRole: true, status: true, externalId: true, platformId: true });
exports.AuthenticationResponse = exports.UserWithoutPassword.merge(user_identity_1.UserIdentity.pick({ verified: true, firstName: true, lastName: true, email: true, trackEvents: true, newsLetter: true })).merge(zod_1.z.object({
    token: zod_1.z.string(),
    projectId: zod_1.z.string().nullable(),
}));
//# sourceMappingURL=authentication-response.js.map