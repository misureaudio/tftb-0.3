% RUN_CHECKCODE  MLint (checkcode) over every .m file in tftb 0.2.
% Prints TSV:  file  line  id  message
TFTB = 'D:/TOOLBOX/tftb-0.3';
subs = {'mfiles','tests','demos','scripts'};
nfiles = 0; nissues = 0;
for s = 1:numel(subs)
    d = fullfile(TFTB, subs{s});
    files = dir(fullfile(d,'*.m'));
    for i = 1:numel(files)
        p = fullfile(d, files(i).name);
        nfiles = nfiles + 1;
        try
            t = checkcode(p);
            for j = 1:numel(t)
                msg = strrep(t(j).message, char(9), ' ');
                msg = strrep(msg, char(10), ' ');
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
exit(0);
