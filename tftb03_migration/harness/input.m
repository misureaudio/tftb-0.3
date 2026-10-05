function var = input(prompt, varargin)
%INPUT  Headless shim for tftb demos.
% - 's' flag (text prompts like 'y or n :') -> 'y'  (accept / continue)
% - numeric prompts (frequency bounds, N, ...) -> []  (empty), because the
%   toolbox code does 'if isempty(x), x = default; end' and then validates
%   the value. Returning a number would bypass the defaults and can violate
%   fmin<fmax; returning [] lets the documented defaults apply.
s = '';
if ~isempty(varargin) && ischar(varargin{1}), s = varargin{1}; end
if ~isempty(s) && any(s=='s'),
  var = 'y';
else
  var = [];
end
end
