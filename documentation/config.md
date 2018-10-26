# ProvMark configuration

Configuration of ProvMark are done by modifying config/config.ini file.

In ProvMark system, the first two stage is collecting provenance information from provenance collecting tools and transform the provenance result into clingo graph. Different tools need different handle process and type conversion. These config are stored in the config.ini file.
Each profile is start with the name are includes three settings as follow:
- stage1tool: define the script (and parameter) for stage 1 handling when this profile is chosen
- stage2handler: define which graph handler is used to handle the raw provenance information when this profile is chosen
- template: the prefix attached to the working file when this profile is chosen.
- threshold: threshold value set to allow some noise and error in the evaluation stage.

Each profile defines one supporting tools and their configuration. If new tools are support in ProvMark, a new profile will be created here.
