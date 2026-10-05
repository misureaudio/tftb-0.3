function probe_split
v = version;
fprintf('version=[%s]\n', v);
m = sscanf(v, '%d');
fprintf('sscanf(version,%%d) = %g\n', m);
fprintf('major>=5 ? %d\n', m>=5);
% simulate R4
fprintf('sscanf("4.2.1",%%d) = %g\n', sscanf('4.2.1','%d'));
% simulate old R5
fprintf('sscanf("5.3",%%d) = %g\n', sscanf('5.3','%d'));
end
