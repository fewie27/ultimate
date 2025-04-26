import React, { useState, useRef } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress,
  IconButton,
  makeStyles
} from '@material-ui/core';
import { CloudUpload, Delete, PictureAsPdf, Description, Image } from '@material-ui/icons';
import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(3),
    marginBottom: theme.spacing(3),
  },
  uploadBox: {
    border: `2px dashed ${theme.palette.primary.main}`,
    borderRadius: theme.shape.borderRadius,
    padding: theme.spacing(3),
    textAlign: 'center',
    cursor: 'pointer',
    marginBottom: theme.spacing(2),
    backgroundColor: theme.palette.background.default,
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
  },
  filePreview: {
    maxWidth: '100%',
    maxHeight: 200,
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
    boxShadow: theme.shadows[2],
  },
  fileInfo: {
    display: 'flex',
    alignItems: 'center',
    marginTop: theme.spacing(2),
    padding: theme.spacing(2),
    backgroundColor: theme.palette.background.default,
    borderRadius: theme.shape.borderRadius,
  },
  fileIcon: {
    marginRight: theme.spacing(2),
    color: theme.palette.primary.main,
  },
  fileName: {
    flex: 1,
  },
  hidden: {
    display: 'none',
  },
  submitButton: {
    marginTop: theme.spacing(2),
  },
  successBox: {
    marginTop: theme.spacing(2),
    padding: theme.spacing(2),
    backgroundColor: theme.palette.success.light,
    borderRadius: theme.shape.borderRadius,
  },
}));

const FileUpload = ({ onUploadSuccess }) => {
  const classes = useStyles();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisId, setAnalysisId] = useState('');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setError('');

    // Create preview for images
    if (selectedFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      setError('');

      // Create preview for images
      if (droppedFile.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => {
          setPreview(reader.result);
        };
        reader.readAsDataURL(droppedFile);
      } else {
        setPreview(null);
      }
    }
  };

  const handleUpload = async () => {
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
      if (onUploadSuccess) {
        onUploadSuccess(response.data.id);
      }
      setLoading(false);
    } catch (err) {
      setError('Fehler beim Hochladen: ' + (err.response?.data?.error || err.message));
      setLoading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreview(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getFileIcon = () => {
    if (!file) return null;
    
    if (file.type.includes('pdf')) {
      return <PictureAsPdf className={classes.fileIcon} fontSize="large" />;
    } else if (file.type.includes('word') || file.type.includes('document')) {
      return <Description className={classes.fileIcon} fontSize="large" />;
    } else if (file.type.includes('image')) {
      return <Image className={classes.fileIcon} fontSize="large" />;
    } else {
      return <Description className={classes.fileIcon} fontSize="large" />;
    }
  };

  return (
    <Paper className={classes.root}>
      <Typography variant="h6" gutterBottom>
        Dokument hochladen
      </Typography>

      {error && (
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      )}

      <input
        type="file"
        onChange={handleFileChange}
        accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
        className={classes.hidden}
        ref={fileInputRef}
        id="file-upload-input"
      />

      <label htmlFor="file-upload-input">
        <Box
          className={classes.uploadBox}
          component="div"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
        >
          <CloudUpload color="primary" style={{ fontSize: 48, marginBottom: 8 }} />
          <Typography variant="body1" gutterBottom>
            Datei hier ablegen oder klicken zum Auswählen
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Unterstützte Formate: PDF, DOCX, TXT, JPG, PNG
          </Typography>
        </Box>
      </label>

      {file && (
        <>
          {preview && (
            <Box display="flex" justifyContent="center">
              <img src={preview} alt="Vorschau" className={classes.filePreview} />
            </Box>
          )}

          <Paper className={classes.fileInfo}>
            {getFileIcon()}
            <Typography className={classes.fileName} variant="body2">
              {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </Typography>
            <IconButton size="small" onClick={handleRemoveFile}>
              <Delete />
            </IconButton>
          </Paper>

          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleUpload}
            disabled={loading}
            className={classes.submitButton}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Wird hochgeladen...' : 'Dokument analysieren'}
          </Button>
        </>
      )}

      {analysisId && (
        <Box className={classes.successBox}>
          <Typography variant="subtitle1">
            Dokument hochgeladen. Ihre Analyse-ID:
          </Typography>
          <Typography variant="h6" color="primary">
            {analysisId}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default FileUpload; 