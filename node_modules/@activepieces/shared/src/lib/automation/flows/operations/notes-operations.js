"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.notesOperations = void 0;
const tslib_1 = require("tslib");
const dayjs_1 = tslib_1.__importDefault(require("dayjs"));
const _updateNote = (flowVersion, request) => {
    const newFlowVersion = JSON.parse(JSON.stringify(flowVersion));
    newFlowVersion.notes = newFlowVersion.notes.map((note) => {
        if (note.id === request.id) {
            return Object.assign(Object.assign(Object.assign({}, note), request), { updatedAt: (0, dayjs_1.default)().toISOString() });
        }
        return note;
    });
    return newFlowVersion;
};
const _deleteNote = (flowVersion, request) => {
    const newFlowVersion = JSON.parse(JSON.stringify(flowVersion));
    newFlowVersion.notes = newFlowVersion.notes.filter((note) => note.id !== request.id);
    return newFlowVersion;
};
const _addNote = (flowVersion, request) => {
    const newFlowVersion = JSON.parse(JSON.stringify(flowVersion));
    newFlowVersion.notes.push(Object.assign(Object.assign({}, request), { createdAt: (0, dayjs_1.default)().toISOString(), updatedAt: (0, dayjs_1.default)().toISOString() }));
    return newFlowVersion;
};
exports.notesOperations = {
    updateNote: _updateNote,
    deleteNote: _deleteNote,
    addNote: _addNote,
};
//# sourceMappingURL=notes-operations.js.map