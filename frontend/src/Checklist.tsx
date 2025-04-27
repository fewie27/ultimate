import React from "react";
import { CheckCircle, XCircle } from "lucide-react";
import { motion } from "framer-motion";

export type ChecklistItem = {
    title: string;
    description: string;
    completed: boolean;
};
type ChecklistProps = {
    checklistItems: ChecklistItem[];
    onClose?: () => void;
};

export default function Checklist({ checklistItems, onClose }: ChecklistProps) {

    return (
        <div className="popup_background">
            <motion.div
                className="popup flex flex-col gap-6 p-8 bg-gray-100 rounded-lg"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <h1 className="text-2xl font-bold text-center mb-6">Checklist: Essentials / Key Contract Clauses</h1>
                {checklistItems.map((item, index) => (
                    <motion.div
                        key={index}
                        className="flex items-start gap-4"
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: 0.1 * index }}
                    >
                        <div className={`flex items-center justify-center w-10 h-10 rounded-full ${item.completed ? 'bg-green-400' : 'bg-red-400'}`}>
                            {item.completed ? (
                                <CheckCircle className="text-white" size={24} style={{ color: "green" }}/>
                            ) : (
                                <XCircle className="text-white" size={24}  style={{ color: "red" }}/>
                            )}
                        </div>
                        <div>
                            <h3 className="text-lg font-bold">{item.title}</h3>
                            <p className="text-gray-700 text-sm">{item.description}</p>
                        </div>
                    </motion.div>
                ))}
                <button style={styles.okayButton} onClick={onClose}>
                    Okay
                </button>
            </motion.div>
        </div>
    );
}

const styles: { [key: string]: React.CSSProperties } = {
    okayButton: {
        marginTop: "30px",
        backgroundColor: "#F25D00",
        color: "#fff",
        border: "none",
        padding: "12px 24px",
        fontSize: "16px",
        borderRadius: "8px",
        cursor: "pointer",
        width: "200px",
        marginLeft: "auto",
        marginRight: "auto",
        display: "block"
    },
}