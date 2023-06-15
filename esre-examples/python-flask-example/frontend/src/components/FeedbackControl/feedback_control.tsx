import React, { useState } from "react";
import "./_feedback_control.scss";

import { Smile } from "../images/smile";
import { Neutral } from "../images/neutral";
import { Disappointed } from "../images/disappointed";
import { Bug } from "../images/bug";

export const FeedbackControl = () => {
  const [selected, setSelected] = useState<number | undefined>(undefined);

  const buttons: any[] = ["smile", "disappointed", "bug"];
  interface ButtonProps {
    icon: string;
    onClick: any;
  }
  const Button: React.FC<ButtonProps> = ({ icon, onClick }) => (
    <button
      onClick={onClick}
      className={`feedbackControl__button ${
        selected === buttons.indexOf(icon) ? "isSelected" : ""
      }`}
    >
      {icon === "smile" && <Smile />}
      {icon === "disappointed" && <Disappointed />}
      {icon === "bug" && <Bug />}
    </button>
  );

  return (
    <div className="feedbackControl__wrapper">
      {buttons.map((btn, index) => (
        <Button icon={btn} key={btn} onClick={() => setSelected(index)} />
      ))}
    </div>
  );
};
