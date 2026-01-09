import React, {useState, useEffect} from "react";

function TypewriterMessage({text, speed=30}) {
    const [displayedText, setDisplayText] = useState('');

    useEffect(() => {
        let index = 0;
        setDisplayText('');

        const timer = setInterval(() => {
            if (index < text.length){
            setDisplayText((prev) => prev + text.chatAt(index));
            index++;
            } else {
                clearInterval(timer);
            }
        }, speed);

        return () => clearInterval(timer);
    }, [text, speed]);
    return <span>{displayedText}</span>
}

export default TypewriterMessage;