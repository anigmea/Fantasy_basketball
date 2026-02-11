import React from 'react';
import { PlayerTable, Player } from '../components/PlayerTable';
import { Center, Circle, Group, Square, Box } from "@chakra-ui/react"

// Sample data matching your screenshot
const samplePlayers: Player[] = [
  {
    id: '1',
    name: 'Shaedon Sharpe',
    team: 'BOS',
    position: 'SF',
    status: 'OUT',
    avgPoints: 18,
    projectedAvg: 18,
    ranking: 15,
    gamesLeftWeek: 2,
  },
  {
    id: '2',
    name: 'Shaedon Sharpe',
    team: 'BOS',
    position: 'SF',
    status: 'DTD',
    avgPoints: 18,
    projectedAvg: 18,
    ranking: 15,
    gamesLeftWeek: 2,
  },
  {
    id: '3',
    name: 'Shaedon Sharpe',
    team: 'BOS',
    position: 'SF',
    status: 'SUSPEND',
    avgPoints: 18,
    projectedAvg: 18,
    ranking: 15,
    gamesLeftWeek: 2,
  },
  {
    id: '4',
    name: 'LeBron James',
    team: 'LAL',
    position: 'SF',
    status: 'ACTIVE',
    avgPoints: 25.2,
    projectedAvg: 24.8,
    ranking: 3,
    gamesLeftWeek: 3,
  },
  {
    id: '5',
    name: 'Stephen Curry',
    team: 'GSW',
    position: 'PG',
    status: 'ACTIVE',
    avgPoints: 26.8,
    projectedAvg: 27.1,
    ranking: 1,
    gamesLeftWeek: 4,
  },
  {
    id: '6',
    name: 'Kevin Durant',
    team: 'PHX',
    position: 'PF',
    status: 'QUESTIONABLE',
    avgPoints: 28.3,
    projectedAvg: 27.5,
    ranking: 2,
    gamesLeftWeek: 2,
  },
];



export const Replacements: React.FC = () => {
  return (
    <Group  style={{width: '100vw', justifyContent: 'center', alignItems: 'flex-start', gap: '40px'}} flexDirection={{ smToLg: 'column'}}>
      <Box style={{padding: '40px', height: 'fit-content', backgroundColor: '#0a0a0a'}} width={{ smToLg: '100%', lg: '40%' }}>
        <h1 style={{ 
          color: '#ffffff', 
          marginBottom: '12px',
          fontSize: '32px',
          fontWeight: '700',
          textAlign: 'center',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
        }}>
          Injured Players
        </h1>
        <p style={{ 
          textAlign: 'center',
          color: '#999999', 
          marginBottom: '32px',
          fontSize: '14px',
        }}>
          Click player to find replacement
        </p>
        <PlayerTable 
          players={samplePlayers} 
          columns={['player', 'status', 'position', 'avgPoints']}
        />
      </Box>
      <Box style={{padding: '40px', backgroundColor: '#0a0a0a', height: 'fit-content'}} width={{ smToLg: '100%', lg: '50%' }}>
        <h1 style={{ 
          color: '#ffffff', 
          marginBottom: '12px',
          fontSize: '32px',
          fontWeight: '700',
          textAlign: 'center',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
        }}>
          Replacement Candidates
        </h1>
        <p style={{ 
          textAlign: 'center',
          color: '#999999', 
          marginBottom: '32px',
          fontSize: '14px',
        }}>
          Showing results for...
        </p>
        <PlayerTable 
        players={samplePlayers} 
        columns={['player', 'position', 'avgPoints', 'projectedAvg', 'gamesLeftWeek']}
        />
      </Box>
    </Group>
    
    
  );
};

export default Replacements;