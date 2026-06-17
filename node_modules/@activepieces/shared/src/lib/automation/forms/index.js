"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatFormResponse = exports.HumanInputFormResult = exports.HumanInputFormResultTypes = exports.FileResponseInterface = void 0;
exports.createKeyForFormInput = createKeyForFormInput;
const zod_1 = require("zod");
const FileResponseInterfaceV1 = zod_1.z.object({
    base64Url: zod_1.z.string(),
    fileName: zod_1.z.string(),
    extension: zod_1.z.string().optional(),
});
const FileResponseInterfaceV2 = zod_1.z.object({
    mimeType: zod_1.z.string(),
    url: zod_1.z.string(),
    fileName: zod_1.z.string().optional(),
});
exports.FileResponseInterface = zod_1.z.union([FileResponseInterfaceV1, FileResponseInterfaceV2]);
var HumanInputFormResultTypes;
(function (HumanInputFormResultTypes) {
    HumanInputFormResultTypes["FILE"] = "file";
    HumanInputFormResultTypes["MARKDOWN"] = "markdown";
})(HumanInputFormResultTypes || (exports.HumanInputFormResultTypes = HumanInputFormResultTypes = {}));
function createKeyForFormInput(displayName) {
    const inputKey = displayName
        .toLowerCase()
        .replace(/\s+(\w)/g, (_, letter) => letter.toUpperCase())
        .replace(/^(.)/, letter => letter.toLowerCase());
    /**We do this because react form inputs must not contain quotes */
    return inputKey.replaceAll(/[\\"''\n\r\t]/g, '');
}
exports.HumanInputFormResult = zod_1.z.union([
    zod_1.z.object({
        type: zod_1.z.literal(HumanInputFormResultTypes.FILE),
        value: exports.FileResponseInterface,
    }),
    zod_1.z.object({
        type: zod_1.z.literal(HumanInputFormResultTypes.MARKDOWN),
        value: zod_1.z.string(),
        files: zod_1.z.array(exports.FileResponseInterface).optional(),
    }),
]);
exports.ChatFormResponse = zod_1.z.object({
    sessionId: zod_1.z.string(),
    message: zod_1.z.string(),
    files: zod_1.z.array(zod_1.z.string()).optional(),
});
//# sourceMappingURL=index.js.map