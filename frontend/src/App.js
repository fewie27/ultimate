import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { Container, Typography, Box, Button, TextField, Paper, List, ListItem, ListItemText, Divider, CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import axios from 'axios';
import './App.css';

const useStyles = makeStyles((theme) => ({
  title: {
    marginBottom: theme.spacing(4),
  },
  uploadForm: {
    marginBottom: theme.spacing(4),
  },
  fileInput: {
    marginBottom: theme.spacing(2),
  },
  paper: {
    padding: theme.spacing(3),
    marginBottom: theme.spacing(3),
  },
  analysisItem: {
    padding: theme.spacing(2),
    marginBottom: theme.spacing(2),
    backgroundColor: (props) => {
      switch (props.category) {
        case 'fehlend': return '#e3f2fd';
        case 'ungewöhnlich': return '#fff9c4';
        case 'nichtig': return '#ffcdd2';
        default: return '#ffffff';
      }
    },
  },
  category: {
    fontWeight: 'bold',
    marginBottom: theme.spacing(1),
  },
  description: {
    fontStyle: 'italic',
    color: theme.palette.text.secondary,
  },
  analysisId: {
    marginBottom: theme.spacing(2),
  },
}));

function AnalysisItem({ item }) {
  const classes = useStyles(item);
  
  return (
    <Paper className={classes.analysisItem} elevation={1}>
      <Typography variant="body1">{item.text}</Typography>
      <Typography className={classes.category} variant="subtitle2">
        Kategorie: {item.category}
      </Typography>
      <Typography className={classes.description} variant="body2">
        {item.description}
      </Typography>
    </Paper>
  );
}

function Home() {
  const classes = useStyles();
  const [file, setFile] = useState(null);
  const [analysisId, setAnalysisId] = useState('');
  const [lookupId, setLookupId] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };
  
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Bitte wählen Sie eine Datei aus');
      return;
    }
    
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setAnalysisId(response.data.id);
      setLookupId(response.data.id);
      setLoading(false);
    } catch (err) {
      setError('Fehler beim Hochladen: ' + (err.response?.data?.error || err.message));
      setLoading(false);
    }
  };
  
  const handleLookup = async (e) => {
    e.preventDefault();
    if (!lookupId) {
      setError('Bitte geben Sie eine Analyse-ID ein');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`/api/analysis/${lookupId}`);
      setAnalysisResults(response.data);
      setLoading(false);
    } catch (err) {
      setError('Fehler beim Abrufen der Analyse: ' + (err.response?.data?.error || err.message));
      setLoading(false);
      setAnalysisResults(null);
    }
  };
  
  return (
    <Container maxWidth="md">
      <Box my={4}>
        <Typography variant="h4" component="h1" className={classes.title} gutterBottom>
          Rechtsdokument-Analyse
        </Typography>
        
        {error && (
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
        )}
        
        <Paper className={classes.paper}>
          <Typography variant="h6" gutterBottom>
            Dokument hochladen
          </Typography>
          <form className={classes.uploadForm} onSubmit={handleUpload}>
            <Box className={classes.fileInput}>
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx,.txt"
              />
            </Box>
            <Button
              variant="contained"
              color="primary"
              type="submit"
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Hochladen'}
            </Button>
          </form>
          
          {analysisId && (
            <Box mt={2}>
              <Typography variant="subtitle1">
                Dokument hochgeladen. Ihre Analyse-ID:
              </Typography>
              <Typography variant="h6" color="primary">
                {analysisId}
              </Typography>
            </Box>
          )}
        </Paper>
        
        <Paper className={classes.paper}>
          <Typography variant="h6" gutterBottom>
            Analyse abrufen
          </Typography>
          <form onSubmit={handleLookup}>
            <TextField
              label="Analyse-ID"
              variant="outlined"
              fullWidth
              value={lookupId}
              onChange={(e) => setLookupId(e.target.value)}
              className={classes.fileInput}
            />
            <Button
              variant="contained"
              color="primary"
              type="submit"
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Abrufen'}
            </Button>
          </form>
        </Paper>
        
        {analysisResults && (
          <Paper className={classes.paper}>
            <Typography variant="h6" gutterBottom>
              Analyseergebnisse
            </Typography>
            <Typography className={classes.analysisId} variant="subtitle1">
              Analyse-ID: {analysisResults.id}
            </Typography>
            
            {analysisResults.results.length === 0 ? (
              <Typography>Keine Ergebnisse gefunden.</Typography>
            ) : (
              <Box>
                {analysisResults.results.map((item, index) => (
                  <AnalysisItem key={index} item={item} />
                ))}
              </Box>
            )}
          </Paper>
        )}
      </Box>
    </Container>
  );
}

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" component={Home} />
      </Switch>
    </Router>
  );
}

export default App; 