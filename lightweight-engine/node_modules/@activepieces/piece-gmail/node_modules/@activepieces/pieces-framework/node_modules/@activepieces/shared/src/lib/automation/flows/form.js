"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.USE_DRAFT_QUERY_PARAM_NAME = exports.ChatUIResponse = exports.ChatUIProps = exports.FormResponse = exports.FormProps = exports.FormInput = exports.FormInputType = void 0;
const zod_1 = require("zod");
var FormInputType;
(function (FormInputType) {
    FormInputType["TEXT"] = "text";
    FormInputType["FILE"] = "file";
    FormInputType["TEXT_AREA"] = "text_area";
    FormInputType["TOGGLE"] = "toggle";
})(FormInputType || (exports.FormInputType = FormInputType = {}));
exports.FormInput = zod_1.z.object({
    displayName: zod_1.z.string(),
    required: zod_1.z.boolean(),
    description: zod_1.z.string(),
    type: zod_1.z.nativeEnum(FormInputType),
});
exports.FormProps = zod_1.z.object({
    inputs: zod_1.z.array(exports.FormInput),
    waitForResponse: zod_1.z.boolean(),
});
exports.FormResponse = zod_1.z.object({
    id: zod_1.z.string(),
    title: zod_1.z.string(),
    props: exports.FormProps,
    projectId: zod_1.z.string(),
    version: zod_1.z.string(),
});
exports.ChatUIProps = zod_1.z.object({
    botName: zod_1.z.string(),
});
exports.ChatUIResponse = zod_1.z.object({
    id: zod_1.z.string(),
    title: zod_1.z.string(),
    props: exports.ChatUIProps,
    projectId: zod_1.z.string(),
    platformLogoUrl: zod_1.z.string(),
    platformName: zod_1.z.string(),
});
exports.USE_DRAFT_QUERY_PARAM_NAME = 'useDraft';
//# sourceMappingURL=form.js.map