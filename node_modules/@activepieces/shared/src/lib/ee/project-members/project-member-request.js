"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GetCurrentProjectMemberRoleQuery = exports.UpdateProjectMemberRoleRequestBody = exports.AcceptProjectResponse = exports.ListProjectMembersRequestQuery = exports.AcceptInvitationRequest = void 0;
const zod_1 = require("zod");
exports.AcceptInvitationRequest = zod_1.z.object({
    token: zod_1.z.string(),
});
exports.ListProjectMembersRequestQuery = zod_1.z.object({
    projectId: zod_1.z.string(),
    projectRoleId: zod_1.z.string().optional(),
    cursor: zod_1.z.string().optional(),
    limit: zod_1.z.coerce.number().optional(),
});
exports.AcceptProjectResponse = zod_1.z.object({
    registered: zod_1.z.boolean(),
});
exports.UpdateProjectMemberRoleRequestBody = zod_1.z.object({
    role: zod_1.z.string(),
});
exports.GetCurrentProjectMemberRoleQuery = zod_1.z.object({
    projectId: zod_1.z.string(),
});
//# sourceMappingURL=project-member-request.js.map