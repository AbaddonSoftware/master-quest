// components/TextField.tsx
import * as React from "react";

type Props = Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange" | "value"> & {
  label?: string;
  value?: string;
  onChange?: (v: string) => void;
};

export default function TextField({ label, value, onChange, ...rest }: Props) {
  return (
    <label>
      {label && <span>{label}<br/></span>}
      <input
        {...rest}
        value={value ?? ""}
        onChange={(e) => onChange?.(e.currentTarget.value)}
      />
    </label>
  );
}


// type Props = React.InputHTMLAttributes<HTMLInputElement> & { label?: string };
// export default function TextField({ label, ...rest }: Props) {
//   return (
//     <label style={{ display: "block" }}>
//       {label && <span>{label}<br/></span>}
//       <input {...rest} />
//     </label>
//   );
// }
