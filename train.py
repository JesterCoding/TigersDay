import argparse
import os
from ai.trainer import Trainer
from ai.model import save_checkpoint, load_checkpoint


def main():
    parser = argparse.ArgumentParser(description="Train AlphaZero AI for The Tiger's Day")
    parser.add_argument('--iterations', type=int, default=100,
                        help="Number of training iterations")
    parser.add_argument('--games', type=int, default=50,
                        help="Self-play games per iteration")
    parser.add_argument('--simulations', type=int, default=100,
                        help="MCTS simulations per move")
    parser.add_argument('--batch-size', type=int, default=256,
                        help="Training batch size")
    parser.add_argument('--lr', type=float, default=1e-3,
                        help="Learning rate")
    parser.add_argument('--resume', type=str, default=None,
                        help="Path to checkpoint to resume from")
    args = parser.parse_args()

    config = {
        'lr': args.lr,
        'l2_reg': 1e-4,
        'buffer_size': 50000,
        'num_simulations': args.simulations,
        'batch_size': args.batch_size,
        'num_games_per_iteration': args.games,
        'num_training_steps': 100,
        'num_iterations': args.iterations,
        'temperature_threshold': 15,
        'checkpoint_dir': 'ai/checkpoints/',
    }

    # Ensure checkpoint directory exists
    os.makedirs(config['checkpoint_dir'], exist_ok=True)

    trainer = Trainer(config)

    start_iter = 0
    if args.resume:
        start_iter = load_checkpoint(trainer.model, trainer.optimizer, args.resume)
        print(f"Resumed from iteration {start_iter}")

    for i in range(start_iter, config['num_iterations']):
        trainer.run_iteration(i)

        # Save best model every 10 iterations
        if (i + 1) % 10 == 0:
            save_checkpoint(
                trainer.model, trainer.optimizer, i,
                f"{config['checkpoint_dir']}best_model.pth"
            )
            print(f"Saved best model at iteration {i + 1}")

    print("Training complete.")


if __name__ == "__main__":
    main()
