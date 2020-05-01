use std::fmt::Display;
use std::path::{Path, PathBuf};
use std::rc::Rc;

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
    config: Rc<Config>,
}

impl Display for Project {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "<Project {}>", self.name)
    }
}

impl Project {
    fn build(&self) {
        println!("Building {} with config {:?}", self, self.config);
    }
}

#[derive(Debug)]
struct Workspace {
    root_path: PathBuf,
    config: Rc<Config>,
    projects: Vec<Project>,
}

impl Workspace {
    fn new(root_path: &Path) -> Workspace {
        let config = Rc::new(parse_config(root_path));
        let mut res = Workspace {
            root_path: root_path.to_path_buf(),
            projects: vec![],
            config: Rc::clone(&config),
        };
        res.projects = Rc::clone(&config)
            .projects
            .iter()
            .map(|x| res.new_project(x))
            .collect();
        res
    }

    fn new_project(&self, name: &str) -> Project {
        Project {
            name: name.to_string(),
            path: self.root_path.join(name),
            config: Rc::clone(&self.config),
        }
    }
}

fn main() {
    let root_path = PathBuf::from("path/to/Workspace");
    let workspace = Workspace::new(&root_path);
    dbg!(&workspace);
    for project in workspace.projects {
        project.build()
    }
}
