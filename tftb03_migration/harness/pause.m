function pause(varargin)
%PAUSE  Headless shim: defer to the real built-in (non-blocking).
builtin('pause', 0);
end
