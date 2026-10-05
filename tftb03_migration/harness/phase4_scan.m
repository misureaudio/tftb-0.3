% PHASE4_SCAN  Full mlint (checkcode) scan of tftb-0.3.
% checkcode (R2024a) struct has fields: message, fix, line, column  (NO id).
% So we bucket by a normalized message prefix instead of a check id.
% Prints TSV:  file  sub  line  message
% then CHECKCODE_SUMMARY and a CHECKCODE_BY_MSG breakdown (count desc).
TFTB = 'D:/TOOLBOX/tftb-0.3';
subs = {'mfiles','tests','demos','scripts'};
nfiles = 0; nissues = 0;
msgcounts = containers.Map('KeyType','char','ValueType','double');
for s = 1:numel(subs)
    d = fullfile(TFTB, subs{s});
    if ~isdir(d), continue; end
    files = dir(fullfile(d,'*.m'));
    for i = 1:numel(files)
        p = fullfile(d, files(i).name);
        nfiles = nfiles + 1;
        try
            t = checkcode(p);
            for j = 1:numel(t)
                msg = strrep(t(j).message, char(9), ' ');
                msg = strrep(msg, char(10), ' ');
                key = msg(1:min(48,end));
                key = regexprep(key, '\s+', ' ');
                if ~msgcounts.isKey(key), msgcounts(key) = 0; end
                msgcounts(key) = msgcounts(key) + 1;
                fprintf('%s\t%s\t%d\t%s\n', files(i).name, subs{s}, t(j).line, msg);
                nissues = nissues + 1;
            end
        catch ME
            fprintf('%s\t%s\t0\tCHECKCODE_ERROR %s\n', files(i).name, subs{s}, ME.message);
            nissues = nissues + 1;
        end
    end
end
fprintf('CHECKCODE_SUMMARY files=%d issues=%d\n', nfiles, nissues);
keys = msgcounts.keys;
vals = cell2mat(msgcounts.values);
[~, ord] = sort(vals,'descend');
keys = keys(ord); vals = vals(ord);
fprintf('CHECKCODE_BY_MSG\n');
for k = 1:numel(keys)
    fprintf('  %6d  %s\n', vals(k), keys{k});
end
exit(0);
