use std::fmt::Display;
use std::path::{Path, PathBuf};

fn parse_config(_root_path: &Path) -> Config {
    Config {
        projects: vec!["foo".to_string(), "bar".to_string()],
    }
}

#[derive(Debug)]
struct Config {
    projects: Vec<String>,
}

#[derive(Debug)]
struct Project {
    name: String,
    path: PathBuf,
}

impl Display for Project {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "<Project {}>", self.name)
    }
}

#[derive(Debug)]
struct Workspace {
    root_path: PathBuf,
    config: Config,
    projects: Vec<Project>,
}

impl Workspace {
    fn new(root_path: &Path) -> Workspace {
        let config = parse_config(root_path);
        // this clone() is a hint something is wrong
        let project_names = config.projects.clone();
        let mut res = Workspace {
            root_path: root_path.to_path_buf(),
            projects: vec![],
            config: config,
        };
        res.projects = project_names.iter().map(|x| res.new_project(x)).collect();
        res
    }

    fn new_project(&self, name: &str) -> Project {
        Project {
            name: name.to_string(),
            path: self.root_path.join(name),
        }
    }
}

fn main() {
    let root_path = PathBuf::from("path/to/Workspace");
    let workspace = Workspace::new(&root_path);
    dbg!(&workspace);
}
