import React, { useCallback } from 'react';
import { BaseEdge, EdgeLabelRenderer, getSmoothStepPath, EdgeProps, useReactFlow } from '@xyflow/react';

export default function ButtonEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data
}: EdgeProps) {
  const { screenToFlowPosition, setEdges } = useReactFlow();

  const handlePointerDown = useCallback((event: React.PointerEvent) => {
    event.stopPropagation();
    
    // Prevent text selection while dragging
    document.body.style.userSelect = 'none';
    
    const onPointerMove = (e: PointerEvent) => {
      const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });
      setEdges((edges) => edges.map((edge) => {
        if (edge.id === id) {
          return { ...edge, data: { ...edge.data, controlPoint: position } };
        }
        return edge;
      }));
    };
    
    const onPointerUp = () => {
      document.body.style.userSelect = '';
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', onPointerUp);
    };
    
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
  }, [id, screenToFlowPosition, setEdges]);

  let edgePath = '';
  let labelX = 0;
  let labelY = 0;

  if (data?.controlPoint) {
      const cp = data.controlPoint as {x: number, y: number};
      // We draw two smooth step paths to pass through the waypoint.
      // From source to control point
      const [path1] = getSmoothStepPath({
          sourceX, sourceY, sourcePosition,
          targetX: cp.x, targetY: cp.y, targetPosition: sourcePosition
      });
      // From control point to target
      const [path2] = getSmoothStepPath({
          sourceX: cp.x, sourceY: cp.y, sourcePosition: targetPosition,
          targetX, targetY, targetPosition
      });
      edgePath = path1 + ' ' + path2;
      labelX = cp.x;
      labelY = cp.y;
  } else {
      const res = getSmoothStepPath({
        sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition
      });
      edgePath = res[0];
      labelX = res[1];
      labelY = res[2];
  }

  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan flex items-center gap-0.5 bg-white p-0.5 rounded-full border border-slate-300 shadow-sm"
        >
          <div 
             className="w-5 h-5 rounded-full cursor-grab active:cursor-grabbing flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
             onPointerDown={handlePointerDown}
             title="Drag to route line"
          >
             <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg>
          </div>
          <button
            className="w-5 h-5 rounded-full flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
            onClick={(event) => {
              event.stopPropagation();
              if (data && typeof data.onDelete === 'function') {
                  data.onDelete(id);
              }
            }}
            title="Delete connection"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
