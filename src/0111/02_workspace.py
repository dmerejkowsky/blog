from path import Path


class Config:
    def __init__(self, project_list):
        self.project_list = project_list

    def __repr__(self):
        return "<Config>"


class Workspace:
    """ A workspace contains a collection of projects
    and a config

    """

    def __init__(self, root_path):
        self.root_path = root_path
        self.config = Config(project_list=["foo", "bar"])
        self.projects = []
        for project_name in self.config.project_list:
            project = self.build_project(project_name)
            self.projects.append(project)

    def build_project(self, name):
        project_path = self.root_path / name
        return Project(name, path=project_path, workspace=self)

    def __repr__(self):
        project_list = ",".join(repr(x) for x in self.projects)
        return f"<Workspace in {self.root_path} with projects {project_list}>"


class Project:
    def __init__(self, name, *, path, workspace):
        self.name = name
        self.path = path
        self.workspace = workspace

    def build(self):
        config = self.workspace.config
        print("building", self.name, "with config", config)

    def __repr__(self):
        # Uncomment me if you dare:
        # return f"<Project {self.name} inside {self.workspace}>"
        return f"<Project {self.name}>"


def main():
    workspace = Workspace(Path("path/to/workspace"))
    print(workspace)
    for project in workspace.projects:
        project.build()


if __name__ == "__main__":
    main()
