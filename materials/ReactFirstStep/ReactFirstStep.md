# 📋 Meta Information

- **date**: 2026/02/~
- **Training Module**: React — First Steps / Component Basics
- **Tag**: #FDETraining #React #JavaScript #Frontend #Component #Hooks
- **Related Notes**: [[materials/ReactFirstStep/problem1-order-processing]] [[materials/ReactFirstStep/problem2-movie-booking]]

---

## 🎯 Goal

- Understand the **React** component model and how UIs are built from components
- Learn **JSX** syntax and how it compiles to JavaScript
- Understand **Props** and **State** management with `useState`
- Handle user events and conditional rendering
- Build simple interactive applications

---

## 📝 Summary

### What is React?

> Overview

A **JavaScript library** for building user interfaces, developed by Meta.

- **Component-based** — UI is split into reusable, self-contained components
- **Declarative** — describe what the UI should look like, React handles the DOM updates
- **Unidirectional data flow** — data flows from parent → child via props

> React vs Vanilla JS

| Aspect | Vanilla JS | React |
|---|---|---|
| DOM manipulation | Manual (`getElementById`) | Declarative (virtual DOM) |
| State management | Manual variables | `useState` hook |
| Reusability | Copy-paste code | Reusable components |
| Scalability | Difficult | ✅ Component tree |

---

### JSX

> What is JSX?

A **syntax extension** that looks like HTML but compiles to `React.createElement()` calls.

```jsx
// JSX
const element = <h1 className="title">Hello World</h1>;

// Compiles to:
const element = React.createElement("h1", { className: "title" }, "Hello World");
```

> JSX Rules

- Use `className` instead of `class`
- All tags must be closed: `<img />`, `<br />`
- Return a single root element (or use `<>...</>` fragment)
- JavaScript expressions go inside `{}`

---

### Components

> Functional Components

```jsx
function Greeting({ name }) {
  return <h1>Hello, {name}!</h1>;
}

// Usage
<Greeting name="Yuichi" />
```

> Props

- **Props** are read-only inputs passed from parent to child
- Like function arguments — cannot be modified inside the component
- Can be any type: string, number, array, object, function

```jsx
function OrderCard({ order, onCancel }) {
  return (
    <div>
      <p>{order.title}</p>
      <button onClick={onCancel}>Cancel</button>
    </div>
  );
}
```

---

### State & Hooks

> `useState`

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);  // [value, setter]

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
    </div>
  );
}
```

> Key Rules of Hooks

- Only call hooks **at the top level** (not inside loops or conditions)
- Only call hooks **inside React functions** (components or custom hooks)

> `useEffect`

Run side effects (API calls, subscriptions) after render:

```jsx
useEffect(() => {
  fetchData();
}, [dependency]); // runs when dependency changes
```

---

### Event Handling

```jsx
function Button() {
  const handleClick = (e) => {
    e.preventDefault();
    console.log("clicked!");
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

- React uses **camelCase** event names: `onClick`, `onChange`, `onSubmit`
- Always pass a **function reference**, not a function call: `onClick={handleClick}` not `onClick={handleClick()}`

---

### Conditional Rendering

```jsx
// Ternary
{isLoggedIn ? <Dashboard /> : <Login />}

// Short-circuit
{error && <ErrorMessage message={error} />}

// Early return
if (loading) return <Spinner />;
```

---

### Lists & Keys

```jsx
const items = ["Apple", "Banana", "Cherry"];

return (
  <ul>
    {items.map((item, index) => (
      <li key={index}>{item}</li>  // key must be unique & stable
    ))}
  </ul>
);
```

> Why keys matter: React uses keys to efficiently update the DOM when lists change.

---

## ❓ Q&A

| Q | A | Clear? |
|---|---|---|
| What is the Virtual DOM? | An in-memory copy of the real DOM; React diffs it to minimize actual DOM updates | ☐ |
| Why can't we modify props? | Props represent the parent's data — modifying them would break unidirectional flow | ☐ |
| When does useEffect run? | After every render by default; specify deps array to control when | ☐ |

---

## 🔤 Word Memo

| Term | Definition | Notes |
|---|---|---|
| component | Reusable, self-contained UI piece | Building block of React apps |
| props | Read-only data passed from parent to child | Like function arguments |
| state | Data that can change inside a component | Managed via `useState` |
| render | React drawing the component to the DOM | Triggered by state/prop changes |
| hook | Function that lets you use state etc. in functional components | Must follow Rules of Hooks |
| JSX | Syntax extension to write HTML-like code in JavaScript | Compiles to `React.createElement` |

---

## ✅ Checklist

- [ ] Can you explain the difference between props and state?
- [ ] Can you explain the deps array in `useEffect`?
- [ ] Can you refactor components for reusability?

---

## 🔗 Graph Links

- 🗺️ MOC: [[MOC]]
- Prev → [[materials/MongoDB_FastAPI/MongoDB_FastAPI]]
- Next → [[materials/React_pagenation/React_Pagination]]
- Related Lecture → [[Lecture/day23-SemanticSearch/System Architecture & Semantic Search]]
- Practice files → [[materials/ReactFirstStep/problem1-order-processing]] / [[materials/ReactFirstStep/problem2-movie-booking]]

### Notes with overlapping concepts
- UI layer for `#concept/microservices` → [[Lecture/day23-SemanticSearch/System Architecture & Semantic Search]]
- Frontend × Agent UI → [[Lecture/day26-Agentic AI & RAG/Agentic AI & RAG]]

### Capstone connection
- Frontend layer → [[Captone/README]]

---

## 🏷️ Tags

`#type/practice` `#domain/frontend`
`#concept/react` `#concept/component` `#concept/hooks`
`#concept/state-management` `#concept/jsx`
`#status/reviewed`
