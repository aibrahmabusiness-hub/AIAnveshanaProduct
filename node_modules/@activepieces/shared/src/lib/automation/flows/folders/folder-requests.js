"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ListFolderRequest = exports.DeleteFolderRequest = exports.UpdateFolderRequest = exports.CreateFolderRequest = void 0;
const zod_1 = require("zod");
exports.CreateFolderRequest = zod_1.z.object({
    displayName: zod_1.z.string(),
    projectId: zod_1.z.string(),
});
exports.UpdateFolderRequest = zod_1.z.object({
    displayName: zod_1.z.string(),
});
exports.DeleteFolderRequest = zod_1.z.object({
    id: zod_1.z.string(),
});
exports.ListFolderRequest = zod_1.z.object({
    limit: zod_1.z.coerce.number().optional(),
    cursor: zod_1.z.string().optional(),
    projectId: zod_1.z.string(),
});
//# sourceMappingURL=folder-requests.js.map