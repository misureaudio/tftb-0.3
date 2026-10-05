function idx = menu(prompt, varargin)
%MENU  Headless shim for tftb demos.
% Returns the index of the menu item that is the "exit" entry — the one
% whose label (case-insensitive) is 'close', 'stop' or 'cancel'. This is
% the universal way out of every tftb interactive menu, regardless of
% position:
%   - tfrqview main menu : 'Close' is the LAST item (12)
%   - tfrrsp / tfrsp etc : 'stop' is the FIRST item (1)
%   - atoms menu         : 'Stop' is the LAST item (5)
% If no such item exists, fall back to the LAST item. No items -> 0.
idx = 0;
if nargin >= 2,
  labels = lower(varargin);
  n = numel(labels);
  for k = 1:n
    lab = labels{k};
    if ischar(lab) && (strcmp(lab,'close') || strcmp(lab,'stop') || strcmp(lab,'cancel'))
      idx = k;
      return;
    end
  end
  idx = n;   % fallback: last item
end
end
