import React from "react";

interface SpeechBubbleContainerProps {
  boardId: string;
}

export const SpeechBubbleContainer: React.FC<SpeechBubbleContainerProps> = ({
  boardId,
}) => {
  // This would contain speech bubble logic for piece interactions
  // For now, it's a placeholder
  return (
    <div
      id={`speech-bubble-container-${boardId}`}
      className="relative aspect-square pointer-events-none"
    >
      {/* Speech bubbles would be rendered here */}
    </div>
  );
};
