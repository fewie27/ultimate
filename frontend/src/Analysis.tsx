import React, { useEffect, useState } from "react";
import axios from "axios";

type Category = "fehlend" | "unusual" | "nichtig" | "match_found" | "";

interface AnalysisItem {
    text: string;
    category: Category;
    description: string;
}

interface AnalysisResponse {
    id: string;
    results: AnalysisItem[];
}

const mockData: AnalysisResponse = {
    id: "mock-id",
    results: [
        {
            text: "Der Mieter darf die Mieträume nur zu Wohnzwecken nutzen.",
            category: "unusual",
            description: "Einschränkung der Nutzung ungewöhnlich restriktiv.",
        },
        {
            text: "Der Vertrag verlängert sich automatisch um weitere 12 Monate.",
            category: "nichtig",
            description: "Automatische Verlängerungsklausel mit ungewöhnlich langer Dauer.",
        },
        {
            text: "Keine Haustiere erlaubt.",
            category: "fehlend",
            description: "Fehlt eine Ausnahmegenehmigung für Kleintiere.",
        },
    ],
};

interface AnalysisProps {
    id: string;
    backToUpload: () => void;
}

const Analysis: React.FC<AnalysisProps> = ({ id, backToUpload }) => {
    const [fullText, setFullText] = useState<string>("Der Mieter darf die Mieträume nur zu Wohnzwecken nutzen. <mark style=\"background-color:yellow\">Der Vertrag verlängert sich automatisch um weitere 12 Monate.</mark> Keine Haustiere erlaubt.");
    const [findings, setFindings] = useState<AnalysisItem[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<Category | "all">("all");

    const fetchAnalysis = async (analysisId: string) => {
        try {
            const response = await axios.get<AnalysisResponse>(`https://api.stage.ultimate.wiegand.cloud/api/analysis/${analysisId}`);
            console.log(response.data.results);
            setFullText(highlightText(response.data.results));
            setFindings(response.data.results);
        } catch (error) {
            console.error("Error fetching analysis, using mock data:", error);
            setFindings(mockData.results);
        }
    };

    useEffect(() => {
        const analysisId = id;
        fetchAnalysis(analysisId);
    }, []);

    const getColorForCategory = (category: Category): string => {
        switch (category) {
            case "fehlend":
                return "red";
            case "unusual":
                return "yellow";
            case "nichtig":
                return "gray";
            case "match_found":
                return "";
            default:
                return "";
        }
    };

    const highlightText = (findings: AnalysisItem[]): string => {
        let highlightedText = "";

        findings.forEach((finding) => {
            if (finding.category === "match_found" || finding.category === "") {
                highlightedText += finding.text.replace("\n", "<br/>") + " ";
            } else {
                const color = getColorForCategory(finding.category);
                highlightedText += `<mark style="background-color:${color};">${finding.text}</mark>`.replace("\n", "<br/>") + " ";
            }
        });

        return highlightedText;
    };

    const filteredFindings = selectedCategory === "all"
        ? findings.filter(f => f.category !== "" && f.category !== "match_found")
        : findings.filter(f => f.category === selectedCategory);

    return (
        <div style={styles.outerContainer}>
            <button style={styles.backButton} onClick={backToUpload}>
                ←
            </button>
            <div style={styles.main}>

                <h1 style={styles.title}>ULTIMATE</h1>

                <div style={styles.container}>
                    <div style={styles.documentContainer}>
                        <div style={styles.subheader}>Your Rental Agreement</div>
                        <div style={styles.subtitle}>hallo_blabla.pdf</div>
                        <div
                            style={styles.document}
                            dangerouslySetInnerHTML={{ __html: fullText }}
                        />
                    </div>

                    <div style={styles.sidebar}>
                        <div style={styles.buttonGroup}>
                            <button onClick={() => setSelectedCategory("unusual")} style={styles.button}>
                                🤔<br />Check
                            </button>
                            <button onClick={() => setSelectedCategory("nichtig")} style={styles.button}>
                                ❌<br />Invalid
                            </button>
                            <button onClick={() => setSelectedCategory("fehlend")} style={styles.button}>
                                ❓<br />Essentials
                            </button>
                        </div>

                        <div style={styles.findingsList}>
                            {filteredFindings.map((finding, idx) => (
                                <div key={idx} style={styles.findingBox}>
                                    <strong>{finding.category.toUpperCase()}</strong>
                                    <p>{finding.text}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analysis;

const styles: { [key: string]: React.CSSProperties } = {
    outerContainer: {
        width: "100%",
        height: "400px",
        display: "flex",
        flexDirection: "column",
    },
    main: {
        fontFamily: "Lexend, sans-serif",
        backgroundColor: "#17002E",
        flex: 1,
        display: "flex",
        flexDirection: "column",
        paddingTop: "20px"
    },
    title: {
        fontFamily: "Lexend Mega, sans-serif",
        fontSize: "65px",
        color: "#F25D00",
        textAlign: "center",
        margin: "0",
        padding: "20px",
    },
    subheader: {
        fontFamily: "Lexend, sans-serif",
        fontSize: "35px",
        color: "#ffffff",
        textAlign: "center",
        margin: "0",
        paddingTop: "20px",
    },
    subtitle: {
        fontFamily: "Lexend, sans-serif",
        fontSize: "15px",
        color: "#ffffff",
        textAlign: "center",
        margin: "0",
        padding: "0px",
    },
    container: {
        flex: 1,
        display: "flex",
        overflow: "hidden",
        paddingTop: "20px"
    },
    documentContainer: {
        flex: 3,
        overflowY: "auto",
        fontSize: "18px",
        lineHeight: "1.8",
        margin: "20px",
        marginRight: "30px",
        borderRadius: "25px",
        backgroundColor: "#ffffff50",
    },
    document: {
        padding: "40px",
        color: "#ffffff",
        boxSizing: "border-box",
    },
    sidebar: {
        flex: 1,
        overflowY: "auto",
        padding: "20px",
        backgroundColor: "#ffffff50",
        borderRadius: "25px",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        margin: "20px",
    },
    buttonGroup: {
        display: "flex",
        flexWrap: "wrap",
        width: "100%",
    },
    button: {
        width: "45%",
        aspectRatio: "1 / 1",
        border: "none",
        backgroundColor: "#ffffff",
        color: "#000000",
        borderRadius: "8px",
        cursor: "pointer",
        lineHeight: "1.5",
        fontSize: "20px",
        fontWeight: "bold",
        margin: "1%",
        padding: "0",
    },
    findingsList: {
        marginTop: "20px",
        overflowY: "auto",
        flex: 1,
    },
    findingBox: {
        backgroundColor: "#fff",
        padding: "12px",
        borderRadius: "8px",
        marginBottom: "10px",
        boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
    },
    backButton: {
        position: "absolute",
        top: "20px",
        left: "20px",
        width: "50px",
        height: "50px",
        borderRadius: "50%",
        backgroundColor: "#F25D00",
        color: "white",
        border: "none",
        fontSize: "24px",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
    },
};