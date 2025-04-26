import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Button, TextField, List, 
  ListItem, ListItemText, ListItemSecondaryAction, 
  IconButton, Checkbox, Paper, Box, AppBar, Toolbar 
} from '@material-ui/core';
import { Delete, Add } from '@material-ui/icons';
import './App.css';

// Import the API client (will be generated from OpenAPI)
// Note: This will be available after running the generate-api script
// import { ItemsService } from './api';

function App() {
  const [items, setItems] = useState([]);
  const [newItemTitle, setNewItemTitle] = useState('');
  const [loading, setLoading] = useState(true);

  // In a production app, you'd use the generated API client
  // For now, we'll mock the API calls for demo purposes
  useEffect(() => {
    const fetchItems = async () => {
      try {
        // Simulating API call
        // const data = await ItemsService.getItems();
        setItems([
          { id: 1, title: 'Learn Docker', completed: false },
          { id: 2, title: 'Set up React', completed: true },
          { id: 3, title: 'Create OpenAPI spec', completed: false }
        ]);
      } catch (error) {
        console.error('Error fetching items:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []);

  const handleAddItem = async () => {
    if (!newItemTitle.trim()) return;

    try {
      // Simulating API call
      // const newItem = await ItemsService.createItem({ title: newItemTitle });
      const newItem = {
        id: items.length + 1,
        title: newItemTitle,
        completed: false
      };

      setItems([...items, newItem]);
      setNewItemTitle('');
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  const handleToggleItem = async (id) => {
    try {
      const updatedItems = items.map(item => {
        if (item.id === id) {
          // Simulating API call
          // await ItemsService.updateItem(id, { ...item, completed: !item.completed });
          return { ...item, completed: !item.completed };
        }
        return item;
      });

      setItems(updatedItems);
    } catch (error) {
      console.error('Error updating item:', error);
    }
  };

  const handleDeleteItem = async (id) => {
    try {
      // Simulating API call
      // await ItemsService.deleteItem(id);
      setItems(items.filter(item => item.id !== id));
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">
            Todo App
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="md">
        <Box my={4}>
          <Paper>
            <Box p={3}>
              <Typography variant="h5" component="h1" gutterBottom>
                Todo List
              </Typography>
              
              <Box display="flex" mb={3}>
                <TextField
                  fullWidth
                  variant="outlined"
                  value={newItemTitle}
                  onChange={(e) => setNewItemTitle(e.target.value)}
                  placeholder="Add a new task"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddItem()}
                />
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<Add />}
                  onClick={handleAddItem}
                  style={{ marginLeft: '10px' }}
                >
                  Add
                </Button>
              </Box>

              {loading ? (
                <Typography>Loading...</Typography>
              ) : (
                <List>
                  {items.map((item) => (
                    <ListItem key={item.id} dense>
                      <Checkbox
                        edge="start"
                        checked={item.completed}
                        onChange={() => handleToggleItem(item.id)}
                      />
                      <ListItemText
                        primary={item.title}
                        style={{ textDecoration: item.completed ? 'line-through' : 'none' }}
                      />
                      <ListItemSecondaryAction>
                        <IconButton edge="end" onClick={() => handleDeleteItem(item.id)}>
                          <Delete />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          </Paper>
        </Box>
      </Container>
    </div>
  );
}

export default App; 