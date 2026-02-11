import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ICellRendererParams } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './PlayerTable.css';

export interface Player {
  id: string;
  name: string;
  team: string;
  position: string;
  status: 'OUT' | 'DTD' | 'SUSPEND' | 'ACTIVE' | 'QUESTIONABLE';
  avgPoints: number;
  projectedAvg: number;
  ranking: number;
  gamesLeftWeek: number;
}

interface PlayerCellRendererParams extends ICellRendererParams {
  data: Player;
}

// Custom cell renderer for player name with team
const PlayerCellRenderer: React.FC<PlayerCellRendererParams> = ({ data }) => {
  return (
    <div className="player-cell">
      <span className="player-name">{data.name}</span>
      <span className="team-badge">{data.team}</span>
    </div>
  );
};

// Custom cell renderer for status
const StatusCellRenderer: React.FC<PlayerCellRendererParams> = ({ data }) => {
  const statusClass = `status-badge status-${data.status.toLowerCase()}`;
  return <span className={statusClass}>{data.status}</span>;
};

interface PlayerTableProps {
  players: Player[];
}

export const PlayerTable: React.FC<PlayerTableProps> = ({ players }) => {
  const columnDefs = useMemo<ColDef<Player>[]>(
    () => [
      {
        headerName: 'Player',
        field: 'name',
        cellRenderer: PlayerCellRenderer,
        flex: 1,
        minWidth: 100,
        sortable: true,
      },
      {
        headerName: 'Position',
        field: 'position',
        flex: 1,
        minWidth: 100,
        sortable: true,
      },
      {
        headerName: 'Status',
        field: 'status',
        cellRenderer: StatusCellRenderer,
        flex: 1,
        minWidth: 100,
        sortable: true
      },
      {
        headerName: 'Avg. Points',
        field: 'avgPoints',
        flex: 1,
        minWidth: 120,
        sortable: true,
        type: 'numericColumn',
      },
      {
        headerName: 'Projected Avg',
        field: 'projectedAvg',
        flex: 1,
        minWidth: 140,
        sortable: true,
        type: 'numericColumn',
      },
      {
        headerName: 'Ranking',
        field: 'ranking',
        flex: 1,
        minWidth: 100,
        sortable: true,
        type: 'numericColumn',
      },
      {
        headerName: 'Games Left (wk)',
        field: 'gamesLeftWeek',
        flex: 1,
        minWidth: 100,
        sortable: true,
        type: 'numericColumn',
      },
    ],
    []
  );

  const defaultColDef = useMemo<ColDef>(
    () => ({
      resizable: false,
      sortable: true,
      suppressMovable: true,
    }),
    []
  );

  return (
    <div className="player-table-container">
      <div className="ag-theme-alpine-dark player-table">
        <AgGridReact
          rowData={players}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          domLayout="autoHeight"
          suppressCellFocus={true}
          rowHeight={60}
          headerHeight={50}
          animateRows={true}
        />
      </div>
    </div>
  );
};