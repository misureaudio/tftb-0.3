function probe_ver
v = version;
fprintf('class(version)=%s\n', class(v));
tok = strsplit(v, ' ');
fprintf('num tokens=%d  tok1=[%s]\n', numel(tok), tok{1});
parts = strsplit(tok{1}, '.');
fprintf('parts1=[%s]\n', parts{1});
major = str2double(parts{1});
fprintf('major=%g  major>=5? %d\n', major, major>=5);
