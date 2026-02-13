export const initialStore=()=>{
  return{
    message: null,
    todos: [
      {
        id: 1,
        title: "Make the bed",
        background: null,
      },
      {
        id: 2,
        title: "Do my homework",
        background: null,
      }
    ],
    token: '',
    current_user: {},
    isLogged:false,
    course_details: {},
    module_details: {},
    lesson_details: {},
    my_progress: [],
    achievements: [],
     alert: {
      text: '',
      color: '',
      display: false
    }
    
  }
}

export default function storeReducer(store, action = {}) {
  switch(action.type){

    case "set_my_progress":
      return {...store, my_progress: action.payload };

    case "set_achievements":
      return {...store, achievements: action.payload };

    case 'set_achievements':
      return {...store, achievements: Array.isArray(action.payload) ? action.payload: []};
     
    case "set_my_progress":
      return {...store,my_progress: Array.isArray(action.payload) ? action.payload : []};  

    case "course_details":
      return { ...store, course_details: action.payload };

    case "module_details":
      return { ...store, module_details: action.payload };

    case "lesson_details":
      return { ...store, lesson_details: action.payload };

    case "handle_user":
      return { ...store, current_user: action.payload};

    case "handle_token":
      return { ...store, token: action.payload};
    
    case "handle_alert":
      return { ...store, alert: action.payload};


    case "handle_isLogged":
      return { ...store, isLogged: action.payload};  


    case 'set_hello':
      return {...store, message: action.payload };
      
    case 'add_task':

      const { id,  color } = action.payload

      return {...store,
        todos: store.todos.map((todo) => (todo.id === id ? { ...todo, background: color } : todo))
      };
    default:
      throw Error('Unknown action.');
  }    
}
