"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DeleteStoreEntryRequest = exports.GetStoreEntryRequest = exports.PutStoreEntryRequest = void 0;
const zod_1 = require("zod");
const store_entry_1 = require("../store-entry");
exports.PutStoreEntryRequest = zod_1.z.object({
    key: zod_1.z.string().max(store_entry_1.STORE_KEY_MAX_LENGTH),
    value: zod_1.z.any().optional(),
});
exports.GetStoreEntryRequest = zod_1.z.object({
    key: zod_1.z.string(),
});
exports.DeleteStoreEntryRequest = zod_1.z.object({
    key: zod_1.z.string(),
});
//# sourceMappingURL=store-entry-request.js.map