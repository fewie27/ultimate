import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Chip,
  makeStyles 
} from '@material-ui/core';
import { Warning, Error, Info } from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(3),
    marginBottom: theme.spacing(3),
  },
  analysisItem: {
    padding: theme.spacing(2),
    marginBottom: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
    backgroundColor: (props) => {
      switch (props.category) {
        case 'fehlend': return theme.palette.info.light;
        case 'ungewöhnlich': return theme.palette.warning.light;
        case 'nichtig': return theme.palette.error.light;
        default: return theme.palette.background.default;
      }
    },
    borderLeft: (props) => {
      switch (props.category) {
        case 'fehlend': return `5px solid ${theme.palette.info.main}`;
        case 'ungewöhnlich': return `5px solid ${theme.palette.warning.main}`;
        case 'nichtig': return `5px solid ${theme.palette.error.main}`;
        default: return `5px solid ${theme.palette.grey[300]}`;
      }
    },
  },
  chip: {
    marginBottom: theme.spacing(1),
  },
  categoryIcon: {
    marginRight: theme.spacing(1),
  },
  text: {
    whiteSpace: 'pre-wrap',
    marginBottom: theme.spacing(1),
  },
  description: {
    fontStyle: 'italic',
    color: theme.palette.text.secondary,
  },
  noResults: {
    padding: theme.spacing(2),
    textAlign: 'center',
  },
  analysisHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing(2),
  },
  summaryBox: {
    display: 'flex',
    justifyContent: 'space-around',
    marginBottom: theme.spacing(3),
    padding: theme.spacing(2),
    backgroundColor: theme.palette.background.default,
    borderRadius: theme.shape.borderRadius,
  },
  summaryItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
}));

const AnalysisItem = ({ item }) => {
  const classes = useStyles(item);
  
  const getCategoryIcon = () => {
    switch (item.category) {
      case 'fehlend': return <Info />;
      case 'ungewöhnlich': return <Warning />;
      case 'nichtig': return <Error />;
      default: return <Info />;
    }
  };
  
  const getCategoryLabel = () => {
    switch (item.category) {
      case 'fehlend': return 'Fehlend';
      case 'ungewöhnlich': return 'Ungewöhnlich';
      case 'nichtig': return 'Nichtig';
      default: return item.category;
    }
  };
  
  const getChipColor = () => {
    switch (item.category) {
      case 'fehlend': return 'primary';
      case 'ungewöhnlich': return 'default';
      case 'nichtig': return 'secondary';
      default: return 'default';
    }
  };
  
  return (
    <Paper className={classes.analysisItem} elevation={1}>
      <Chip
        icon={getCategoryIcon()}
        label={getCategoryLabel()}
        color={getChipColor()}
        className={classes.chip}
      />
      <Typography variant="body1" className={classes.text}>
        {item.text}
      </Typography>
      <Typography variant="body2" className={classes.description}>
        {item.description}
      </Typography>
    </Paper>
  );
};

const AnalysisResults = ({ analysisId, results, loading, error }) => {
  const classes = useStyles();
  
  if (loading) {
    return (
      <Paper className={classes.root}>
        <Typography variant="h6" gutterBottom>
          Analyseergebnisse werden geladen...
        </Typography>
      </Paper>
    );
  }
  
  if (error) {
    return (
      <Paper className={classes.root}>
        <Typography variant="h6" color="error" gutterBottom>
          Fehler beim Laden der Analyseergebnisse
        </Typography>
        <Typography color="error">{error}</Typography>
      </Paper>
    );
  }
  
  if (!results || !results.length) {
    return (
      <Paper className={classes.root}>
        <Typography variant="h6" gutterBottom>
          Analyseergebnisse
        </Typography>
        <Paper className={classes.noResults}>
          <Typography>Keine Ergebnisse gefunden.</Typography>
        </Paper>
      </Paper>
    );
  }
  
  // Count categories for summary
  const categoryCounts = results.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + 1;
    return acc;
  }, {});
  
  return (
    <Paper className={classes.root}>
      <div className={classes.analysisHeader}>
        <Typography variant="h6">
          Analyseergebnisse
        </Typography>
        {analysisId && (
          <Typography variant="body2" color="textSecondary">
            ID: {analysisId}
          </Typography>
        )}
      </div>
      
      <Box className={classes.summaryBox}>
        <div className={classes.summaryItem}>
          <Chip
            icon={<Error />}
            label={categoryCounts.nichtig || 0}
            color="secondary"
          />
          <Typography variant="caption">Nichtig</Typography>
        </div>
        <div className={classes.summaryItem}>
          <Chip
            icon={<Warning />}
            label={categoryCounts.ungewöhnlich || 0}
            color="default"
          />
          <Typography variant="caption">Ungewöhnlich</Typography>
        </div>
        <div className={classes.summaryItem}>
          <Chip
            icon={<Info />}
            label={categoryCounts.fehlend || 0}
            color="primary"
          />
          <Typography variant="caption">Fehlend</Typography>
        </div>
      </Box>
      
      {results.map((item, index) => (
        <AnalysisItem key={index} item={item} />
      ))}
    </Paper>
  );
};

export default AnalysisResults; 