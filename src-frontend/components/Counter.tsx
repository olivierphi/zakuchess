import {useState} from "react";

type CounterProps = {
  counter: number;
}

export const Counter = ({counter}:CounterProps) => {
  const [count, setCount] = useState(counter);
  return (
    <p className="border-2  solid border-slate-500">
      <button onClick={() => setCount(count + 1)}>+</button>
      &nbsp;&nbsp;&nbsp;
      {count}
      &nbsp;&nbsp;&nbsp;
      <button onClick={() => setCount(count - 1)}>-</button>
    </p>
  )
}
