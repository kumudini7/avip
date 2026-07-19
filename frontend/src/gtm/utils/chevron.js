export function chevronClipPath(index, total, notch = 18) {
  if (total === 1) return 'none';
  if (index === 0) return `polygon(0 0, calc(100% - ${notch}px) 0, 100% 50%, calc(100% - ${notch}px) 100%, 0 100%)`;
  if (index === total - 1) return `polygon(0 0, 100% 0, 100% 100%, 0 100%, ${notch}px 50%)`;
  return `polygon(0 0, calc(100% - ${notch}px) 0, 100% 50%, calc(100% - ${notch}px) 100%, 0 100%, ${notch}px 50%)`;
}
